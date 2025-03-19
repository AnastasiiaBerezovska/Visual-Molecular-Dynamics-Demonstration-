from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock
import psutil  # To get memory usage

class MemoryUsageGraph(BoxLayout):
    def __init__(self, monitor, **kwargs):  # get monitor, but don't pass it to super()
        super().__init__(**kwargs)
        self.monitor = monitor  #  monitor instance

        # the graph
        self.graph = Graph(
            xlabel='Time (s)',
            ylabel='Memory Usage (%)',
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

        #  the plot
        self.plot = MeshLinePlot(color=[0, 1, 0, 1])  # Green line for memory
        self.graph.add_plot(self.plot)

        #  the graph to the layout
        self.add_widget(self.graph)

        #  data storage
        self.memory_data = []

        #  updates
        Clock.schedule_interval(self.update_graph, 1)

    def update_graph(self, dt):
        """Update the memory usage graph every second."""
        memory_usage = psutil.virtual_memory().percent  #  system memory usage
        self.memory_data.append(memory_usage)

        #  last 60 values
        if len(self.memory_data) > 60:
            self.memory_data.pop(0)

        #  plot
        self.plot.points = [(i, usage) for i, usage in enumerate(self.memory_data)]
