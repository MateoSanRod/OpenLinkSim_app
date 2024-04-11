import itertools
import time
import warnings

import matplotlib as mpl
import numpy as np
from matplotlib import _api
from matplotlib.animation import *


class TimedAnimation(Animation):
    """
    `Animation` subclass for time-based animation.

    A new frame is drawn every *interval* milliseconds.

    .. note::

        You must store the created Animation in a variable that lives as long
        as the animation should run. Otherwise, the Animation object will be
        garbage-collected and the animation stops.

    Parameters
    ----------
    fig : `~matplotlib.figure.Figure`
        The figure object used to get needed events, such as draw or resize.
    interval : int, default: 200
        Delay between frames in milliseconds.
    repeat_delay : int, default: 0
        The delay in milliseconds between consecutive animation runs, if
        *repeat* is True.
    repeat : bool, default: True
        Whether the animation repeats when the sequence of frames is completed.
    blit : bool, default: False
        Whether blitting is used to optimize drawing.
    """

    def __init__(self, fig, interval=200, repeat_delay=0, repeat=True,
                 event_source=None, *args, **kwargs):
        self._interval = interval
        self.time = time.time()
        # Undocumented support for repeat_delay = None as backcompat.
        self._repeat_delay = repeat_delay if repeat_delay is not None else 0
        self._repeat = repeat
        # If we're not given an event source, create a new timer. This permits
        # sharing timers between animation objects for syncing animations.
        if event_source is None:
            event_source = fig.canvas.new_timer(interval=self._interval)
        super().__init__(fig, event_source=event_source, *args, **kwargs)

    def _step(self, *args):
        """Handler for getting events."""
        # Extends the _step() method for the Animation class.  If
        # Animation._step signals that it reached the end and we want to
        # repeat, we refresh the frame sequence and return True. If
        # _repeat_delay is set, change the event_source's interval to our loop
        # delay and set the callback to one which will then set the interval
        # back.

        still_going = super()._step(*args)
        elapsed_time = ((time.time() - self.time) * 1000) - self.event_source.interval
        self.event_source.interval = self._interval - (elapsed_time) * .95
        self.time = time.time()

        if not still_going:
            if self._repeat:
                # Restart the draw loop
                self._init_draw()
                self.frame_seq = self.new_frame_seq()
                self.event_source.interval = self._repeat_delay
                return True
            else:
                # We are done with the animation. Call pause to remove
                # animated flags from artists that were using blitting
                self.pause()
                if self._blit:
                    # Remove the resize callback if we were blitting
                    self._fig.canvas.mpl_disconnect(self._resize_id)
                self._fig.canvas.mpl_disconnect(self._close_id)
                self.event_source = None
                return False
        return True

    repeat = _api.deprecate_privatize_attribute("3.7")


class FuncAnimation(TimedAnimation):
    """
    `TimedAnimation` subclass that makes an animation by repeatedly calling
    a function *func*.

    .. note::

        You must store the created Animation in a variable that lives as long
        as the animation should run. Otherwise, the Animation object will be
        garbage-collected and the animation stops.

    Parameters
    ----------
    fig : `~matplotlib.figure.Figure`
        The figure object used to get needed events, such as draw or resize.

    func : callable
        The function to call at each frame.  The first argument will
        be the next value in *frames*.   Any additional positional
        arguments can be supplied using `functools.partial` or via the *fargs*
        parameter.

        The required signature is::

            def func(frame, *fargs) -> iterable_of_artists

        It is often more convenient to provide the arguments using
        `functools.partial`. In this way it is also possible to pass keyword
        arguments. To pass a function with both positional and keyword
        arguments, set all arguments as keyword arguments, just leaving the
        *frame* argument unset::

            def func(frame, art, *, y=None):
                ...

            ani = FuncAnimation(fig, partial(func, art=ln, y='foo'))

        If ``blit == True``, *func* must return an iterable of all artists
        that were modified or created. This information is used by the blitting
        algorithm to determine which parts of the figure have to be updated.
        The return value is unused if ``blit == False`` and may be omitted in
        that case.

    frames : iterable, int, generator function, or None, optional
        Source of data to pass *func* and each frame of the animation

        - If an iterable, then simply use the values provided.  If the
          iterable has a length, it will override the *save_count* kwarg.

        - If an integer, then equivalent to passing ``range(frames)``

        - If a generator function, then must have the signature::

             def gen_function() -> obj

        - If *None*, then equivalent to passing ``itertools.count``.

        In all of these cases, the values in *frames* is simply passed through
        to the user-supplied *func* and thus can be of any type.

    init_func : callable, optional
        A function used to draw a clear frame. If not given, the results of
        drawing from the first item in the frames sequence will be used. This
        function will be called once before the first frame.

        The required signature is::

            def init_func() -> iterable_of_artists

        If ``blit == True``, *init_func* must return an iterable of artists
        to be re-drawn. This information is used by the blitting algorithm to
        determine which parts of the figure have to be updated.  The return
        value is unused if ``blit == False`` and may be omitted in that case.

    fargs : tuple or None, optional
        Additional arguments to pass to each call to *func*. Note: the use of
        `functools.partial` is preferred over *fargs*. See *func* for details.

    save_count : int, optional
        Fallback for the number of values from *frames* to cache. This is
        only used if the number of frames cannot be inferred from *frames*,
        i.e. when it's an iterator without length or a generator.

    interval : int, default: 200
        Delay between frames in milliseconds.

    repeat_delay : int, default: 0
        The delay in milliseconds between consecutive animation runs, if
        *repeat* is True.

    repeat : bool, default: True
        Whether the animation repeats when the sequence of frames is completed.

    blit : bool, default: False
        Whether blitting is used to optimize drawing.  Note: when using
        blitting, any animated artists will be drawn according to their zorder;
        however, they will be drawn on top of any previous artists, regardless
        of their zorder.

    cache_frame_data : bool, default: True
        Whether frame data is cached.  Disabling cache might be helpful when
        frames contain large objects.
    """

    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                 save_count=None, *, cache_frame_data=True, **kwargs):
        if fargs:
            self._args = fargs
        else:
            self._args = ()
        self._func = func
        self._init_func = init_func

        # Amount of framedata to keep around for saving movies. This is only
        # used if we don't know how many frames there will be: in the case
        # of no generator or in the case of a callable.
        self._save_count = save_count
        # Set up a function that creates a new iterable when needed. If nothing
        # is passed in for frames, just use itertools.count, which will just
        # keep counting from 0. A callable passed in for frames is assumed to
        # be a generator. An iterable will be used as is, and anything else
        # will be treated as a number of frames.
        if frames is None:
            self._iter_gen = itertools.count
        elif callable(frames):
            self._iter_gen = frames
        elif np.iterable(frames):
            if kwargs.get('repeat', True):
                self._tee_from = frames

                def iter_frames(frames=frames):
                    this, self._tee_from = itertools.tee(self._tee_from, 2)
                    yield from this

                self._iter_gen = iter_frames
            else:
                self._iter_gen = lambda: iter(frames)
            if hasattr(frames, '__len__'):
                self._save_count = len(frames)
                if save_count is not None:
                    _api.warn_external(
                        f"You passed in an explicit {save_count=} "
                        "which is being ignored in favor of "
                        f"{len(frames)=}."
                    )
        else:
            self._iter_gen = lambda: iter(range(frames))
            self._save_count = frames
            if save_count is not None:
                _api.warn_external(
                    f"You passed in an explicit {save_count=} which is being "
                    f"ignored in favor of {frames=}."
                )
        if self._save_count is None and cache_frame_data:
            _api.warn_external(
                f"{frames=!r} which we can infer the length of, "
                "did not pass an explicit *save_count* "
                f"and passed {cache_frame_data=}.  To avoid a possibly "
                "unbounded cache, frame data caching has been disabled. "
                "To suppress this warning either pass "
                "`cache_frame_data=False` or `save_count=MAX_FRAMES`."
            )
            cache_frame_data = False

        self._cache_frame_data = cache_frame_data

        # Needs to be initialized so the draw functions work without checking
        self._save_seq = []

        super().__init__(fig, **kwargs)

        # Need to reset the saved seq, since right now it will contain data
        # for a single frame from init, which is not what we want.
        self._save_seq = []

    def new_frame_seq(self):
        # Use the generating function to generate a new frame sequence
        return self._iter_gen()

    def new_saved_frame_seq(self):
        # Generate an iterator for the sequence of saved data. If there are
        # no saved frames, generate a new frame sequence and take the first
        # save_count entries in it.
        if self._save_seq:
            # While iterating we are going to update _save_seq
            # so make a copy to safely iterate over
            self._old_saved_seq = list(self._save_seq)
            return iter(self._old_saved_seq)
        else:
            if self._save_count is None:
                frame_seq = self.new_frame_seq()

                def gen():
                    try:
                        while True:
                            yield next(frame_seq)
                    except StopIteration:
                        pass

                return gen()
            else:
                return itertools.islice(self.new_frame_seq(), self._save_count)

    def _init_draw(self):
        super()._init_draw()
        # Initialize the drawing either using the given init_func or by
        # calling the draw function with the first item of the frame sequence.
        # For blitting, the init_func should return a sequence of modified
        # artists.
        if self._init_func is None:
            try:
                frame_data = next(self.new_frame_seq())
            except StopIteration:
                # we can't start the iteration, it may have already been
                # exhausted by a previous save or just be 0 length.
                # warn and bail.
                warnings.warn(
                    "Can not start iterating the frames for the initial draw. "
                    "This can be caused by passing in a 0 length sequence "
                    "for *frames*.\n\n"
                    "If you passed *frames* as a generator "
                    "it may be exhausted due to a previous display or save."
                )
                return
            self._draw_frame(frame_data)
        else:
            self._drawn_artists = self._init_func()
            if self._blit:
                if self._drawn_artists is None:
                    raise RuntimeError('The init_func must return a '
                                       'sequence of Artist objects.')
                for a in self._drawn_artists:
                    a.set_animated(self._blit)
        self._save_seq = []

    def _draw_frame(self, framedata):
        if self._cache_frame_data:
            # Save the data for potential saving of movies.
            self._save_seq.append(framedata)
            self._save_seq = self._save_seq[-self._save_count:]

        # Call the func with framedata and args. If blitting is desired,
        # func needs to return a sequence of any artists that were modified.
        self._drawn_artists = self._func(framedata, *self._args)

        if self._blit:

            err = RuntimeError('The animation function must return a sequence '
                               'of Artist objects.')
            try:
                # check if a sequence
                iter(self._drawn_artists)
            except TypeError:
                raise err from None

            # check each item if it's artist
            for i in self._drawn_artists:
                if not isinstance(i, mpl.artist.Artist):
                    raise err

            self._drawn_artists = sorted(self._drawn_artists,
                                         key=lambda x: x.get_zorder())

            for a in self._drawn_artists:
                a.set_animated(self._blit)

    save_count = _api.deprecate_privatize_attribute("3.7")


def _validate_grabframe_kwargs(savefig_kwargs):
    if mpl.rcParams['savefig.bbox'] == 'tight':
        raise ValueError(
            f"{mpl.rcParams['savefig.bbox']=} must not be 'tight' as it "
            "may cause frame size to vary, which is inappropriate for animation."
        )
    for k in ('dpi', 'bbox_inches', 'format'):
        if k in savefig_kwargs:
            raise TypeError(
                f"grab_frame got an unexpected keyword argument {k!r}"
            )
