import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Dash 앱 초기화
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "F-t Graph Simulator"

# 레이아웃 구성
app.layout = dbc.Container([
    html.Div("AI컴퓨터과 2학년 1반 박서준", className="fw-bold fs-5 mt-3 ms-2"),

    html.H2("힘-시간(F-t) 그래프 시뮬레이터", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("물체의 질량 (kg)"),
            dcc.Slider(id='mass-slider', min=1, max=10, step=0.5, value=5,
                       marks={i: str(i) for i in range(1, 11)}),
            html.Br(),
            html.Label("충돌 시간 (초)"),
            dcc.Slider(id='time-slider', min=0.01, max=1.0, step=0.01, value=0.2,
                       marks={0.01: '0.01', 0.5: '0.5', 1.0: '1.0'}),
        ], md=6),

        dbc.Col([
            dcc.Graph(id='ft-graph'),
            html.Div(id='area-output', className='mt-2 text-center fw-bold'),
        ], md=6),
    ])
], fluid=True)

# F-t 그래프 및 충격량 계산 콜백
@app.callback(
    Output('ft-graph', 'figure'),
    Output('area-output', 'children'),
    Input('mass-slider', 'value'),
    Input('time-slider', 'value')
)
def update_graph(mass, duration):
    delta_v = 10  # 속도 변화 (고정)
    impulse = mass * delta_v  # 충격량 = m * Δv

    # 시간 배열 (전체 1.05초 중 충돌시간 구간 중심에 집중)
    t = np.linspace(0, 1.05, 300)
    t_c = duration / 2  # 충돌 시간 구간 중심
    sigma = duration / 6  # 표준편차 (시간 길이에 비례)

    # 원래 정규분포 모양 힘 (면적=1 맞추기 위한 임시 값)
    f_raw = np.exp(-0.5 * ((t - t_c) / sigma) ** 2)

    # 원래 면적 계산
    dt = t[1] - t[0]
    raw_area = np.sum(f_raw) * dt

    # 여기서 힘 세기 조정 : 면적은 impulse 고정, 
    # 시각화는 힘 = 충격량 / 충돌시간 개념 적용
    # 따라서 그래프 높이는 impulse / duration 비례
    f = (impulse / duration) * (f_raw / np.max(f_raw))  # 최고점이 impulse/duration 되도록 정규화

    # 그래프 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=f, mode='lines', name='힘(F)', line=dict(color='royalblue', width=3)))
    fig.update_layout(
        title='곡선형 힘-시간(F-t) 그래프',
        xaxis=dict(title='시간 (s)', range=[0, 1.05], fixedrange=True),
        yaxis=dict(title='힘 (N)', range=[0, max(1100, impulse/duration * 1.1)], fixedrange=True),
        template='plotly_white'
    )

    # 출력 문구 (충격량 = 힘 × 시간 개념으로 설명)
    avg_force = impulse / duration
    text = (f"충격량 (Impulse): {impulse:.2f} N·s = 힘 (평균) {avg_force:.2f} N × 충돌 시간 {duration:.2f} s\n"
            f"(질량 {mass} kg × 속도변화 {delta_v} m/s)")

    return fig, text

# 실행
if __name__ == '__main__':
    app.run(debug=True)