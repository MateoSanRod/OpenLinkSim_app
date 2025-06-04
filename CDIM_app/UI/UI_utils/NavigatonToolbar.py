from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class CustomToolbar(NavigationToolbar):
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

    def __init__(self, *args, **kwargs):
        super(CustomToolbar, self).__init__(*args, **kwargs)
        self.layout().takeAt(1)