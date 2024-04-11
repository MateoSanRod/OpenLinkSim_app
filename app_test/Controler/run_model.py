from app_test.Model.model import Simulation
from app_test.Model.model import Simulation
from test_utils.timer import get_time
def run_image(view_widget_plot, compiled_input):
    image = Simulation(compiled_input).compute_image()
    view_widget_plot.plot_image(image)


def run_simulation(view_widget_plot, compiled_input):
    simulation = Simulation(compiled_input)
    result = simulation.compute_simulation()
    view_widget_plot.plot_simu(result)
