from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock

class CPUUsageGraph(BoxLayout):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = monitor

        # Graph
        self.graph = Graph(
            xlabel='Time (s)',
            ylabel='CPU Usage (%)',
            x_ticks_minor=1,
            x_ticks_major=5,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            xmin=0,
            xmax=60,
            ymin=0,
            ymax=100,
            border_color=[1, 1, 1, 1],
            tick_color=[0.7, 0.7, 0.7, 1],
            label_options={'color': [1, 1, 1, 1], 'bold': True}
        )

        # the plot
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)

        # the Graph to the layout
        self.add_widget(self.graph)

        # data storage
        self.cpu_data = []

        # the graph update
        Clock.schedule_interval(self.update_graph, 1)

    def update_graph(self, dt):
        # the latest CPU usage
        cpu_usage = self.monitor.get_cpu_usage()
        self.cpu_data.append(cpu_usage)

        # only the last 60 data points
        if len(self.cpu_data) > 60:
            self.cpu_data.pop(0)

        # the plot points
        self.plot.points = [(i, usage) for i, usage in enumerate(self.cpu_data)]
