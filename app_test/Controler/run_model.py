from app_test.Model.model import Simulation


def run_image(app, view_widget_plot, compiled_input):
    image = Simulation(compiled_input).compute_image()
    view_widget_plot.plot_image(image)
    # app.theme_manager.deactivate_ani_controlls()
    app.theme_manager.activate_preview_controlls()


def run_simulation(app, view_widget_plot, compiled_input):
    simulation = Simulation(compiled_input)
    result = simulation.compute_simulation()
    view_widget_plot.plot_simu(result)
    app.theme_manager.activate_ani_controlls()
    app.ui.ani_speed_label.setText(f"{app.plot_widget.ani.speed}x")
