from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class CustomToolbar(NavigationToolbar):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

    def __init__(self, *args, **kwargs):
        super(CustomToolbar, self).__init__(*args, **kwargs)
        self.layout().takeAt(1)  #or more than 1 if you have more buttons