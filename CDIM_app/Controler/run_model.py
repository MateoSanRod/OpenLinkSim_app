from CDIM_app.Model.model import Simulation
from view.opengl_view_widget import ViewWidgetPlot


def run_image(app, view_widget_plot, compiled_input):
    simulation = Simulation(compiled_input)
    image = [simulation.compute_image(is_first_frame=True)]

    view_widget_plot.kill_simulation()
    view_widget_plot.simulation_data = image
    view_widget_plot.display_simulation = False
    app.opengl_widget._set_first_plot_limits(image)
    view_widget_plot.plot_image(image)
    app.theme_manager.deactivate_ani_controlls()
    app.theme_manager.activate_preview_controlls()


def run_simulation(app, view_widget_plot, compiled_input):

    if hasattr(app, "current_simulation"):
        del app.current_simulation

    simulation_time = None
    timestep = 0.0035
    gravity = float(app.ui.gravityLineEdit.text())

    if app.ui.simTimeLineEdit.text() != "":
        simulation_time = float(app.ui.simTimeLineEdit.text())
    if app.ui.timestepLineEdit.text() != "":
        timestep = float(app.ui.timestepLineEdit.text())

    print(simulation_time)
    simulation = Simulation(compiled_input,delta_time_factor=timestep, simu_time=simulation_time)
    simulation.compute_simulation()
    simulation._prepare_joint_tables()
    if app.app_controller.kin_analisys:
        simulation.derivate_output_simulation_data_component("node_coordinates")
        simulation.derivate_output_simulation_data_component("link_angle")
        if "cg_global_cord" in simulation.output_simulation_data[0]:
            simulation.derivate_output_simulation_data_component("cg_global_cord")
        if "link_extra_points" in simulation.output_simulation_data[0]:
            simulation.derivate_output_simulation_data_component("link_extra_points")
    if app.app_controller.dyn_analisys:
        simulation.compute_forces_and_moments(g=gravity)

    result = simulation.output_simulation_data

    app.current_simulation = simulation

    app.opengl_widget._set_first_plot_limits(result)
    view_widget_plot.plot_simu(result)
    app.theme_manager.activate_ani_controlls()

