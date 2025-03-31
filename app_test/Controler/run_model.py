from app_test.Model.model import Simulation
from view.opengl_view_widget import ViewWidgetPlot


def run_image(app, view_widget_plot, compiled_input):
    simulation = Simulation(compiled_input)
    image = [simulation.compute_image()]

    view_widget_plot.kill_simulation()
    view_widget_plot.simulation_data = image
    view_widget_plot.display_simulation = False
    app.opengl_widget._set_first_plot_limits(image)
    view_widget_plot.plot_image(image)
    app.theme_manager.deactivate_ani_controlls()
    app.theme_manager.activate_preview_controlls()

def run_simulation(app, view_widget_plot, compiled_input):
    simulation = Simulation(compiled_input)
    simulation.compute_simulation()
    simulation.derivate_output_simulation_data_component("node_coordinates")
    simulation.derivate_output_simulation_data_component("link_angle")
    simulation.derivate_output_simulation_data_component("cg_global_cord")
    simulation.compute_forces_and_moments()
    result = simulation.output_simulation_data
    app.opengl_widget._set_first_plot_limits(result)
    view_widget_plot.plot_simu(result)

    app.theme_manager.activate_ani_controlls()
