# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DashChartEditor(Component):
    """A DashChartEditor component.


Keyword arguments:

- id (string; optional):
    Dash prop to be registered for use with callbacks.

- annotateOptions (dict; default True):
    Options that drive the available options under the \"Annotate\"
    tree.

    `annotateOptions` is a boolean | dict with keys:

    - text (boolean; optional)

    - shapes (boolean; optional)

    - images (boolean; optional)

- config (dict; default {editable: True}):
    Plotly config options, listed here:
    https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js.

- controlOptions (dict; default True):
    Options that drive the available options under the \"Control\"
    tree.

    `controlOptions` is a boolean | dict with keys:

    - sliders (boolean; optional)

    - menus (boolean; optional)

- dataSources (dict with strings as keys and values of type list; optional):
    Input dataSources for driving the chart editors selections.

- figure (dict; optional):
    Output figure of the chart editor (dcc.Graph esk output).

    `figure` is a dict with keys:

    - data (list of dicts; optional):
        Output data of the chart editor.

    - layout (dict; optional):
        Output layout of the chart editor.

    - frames (list; optional):
        Output frames of the chart editor.

- loadFigure (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    {data, layout, frames} given to the chart, used to populate
    selections and chart when loading.

- logoSrc (string; optional):
    Logo that will be displayed in the chart editor.

- logoStyle (dict; optional):
    Style object of the Logo.

- saveState (boolean; default True):
    When passed True, this will save the current state of the grid to
    `figure`.

- structureOptions (dict; default True):
    Options that drive the available options under the \"Structure\"
    tree.

    `structureOptions` is a boolean | dict with keys:

    - traces (boolean; optional)

    - subplots (boolean; optional)

    - transforms (boolean; optional)

- styleOptions (dict; default True):
    Options that drive the available options under the \"Style\" tree.

    `styleOptions` is a boolean | dict with keys:

    - general (boolean; optional)

    - traces (boolean; optional)

    - axes (boolean; optional)

    - maps (boolean; optional)

    - legend (boolean; optional)

    - colorBars (boolean; optional)

- traceOptions (boolean | number | string | dict | list; optional):
    List of trace options to display."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_chart_editor'
    _type = 'DashChartEditor'
    Figure = TypedDict(
        "Figure",
            {
            "data": NotRequired[typing.Sequence[dict]],
            "layout": NotRequired[dict],
            "frames": NotRequired[typing.Sequence]
        }
    )

    StructureOptions = TypedDict(
        "StructureOptions",
            {
            "traces": NotRequired[bool],
            "subplots": NotRequired[bool],
            "transforms": NotRequired[bool]
        }
    )

    StyleOptions = TypedDict(
        "StyleOptions",
            {
            "general": NotRequired[bool],
            "traces": NotRequired[bool],
            "axes": NotRequired[bool],
            "maps": NotRequired[bool],
            "legend": NotRequired[bool],
            "colorBars": NotRequired[bool]
        }
    )

    AnnotateOptions = TypedDict(
        "AnnotateOptions",
            {
            "text": NotRequired[bool],
            "shapes": NotRequired[bool],
            "images": NotRequired[bool]
        }
    )

    ControlOptions = TypedDict(
        "ControlOptions",
            {
            "sliders": NotRequired[bool],
            "menus": NotRequired[bool]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        dataSources: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Sequence]] = None,
        figure: typing.Optional["Figure"] = None,
        style: typing.Optional[typing.Any] = None,
        config: typing.Optional[dict] = None,
        loadFigure: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        logoSrc: typing.Optional[str] = None,
        logoStyle: typing.Optional[dict] = None,
        structureOptions: typing.Optional[typing.Union[bool, "StructureOptions"]] = None,
        styleOptions: typing.Optional[typing.Union[bool, "StyleOptions"]] = None,
        annotateOptions: typing.Optional[typing.Union[bool, "AnnotateOptions"]] = None,
        controlOptions: typing.Optional[typing.Union[bool, "ControlOptions"]] = None,
        traceOptions: typing.Optional[typing.Any] = None,
        saveState: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'annotateOptions', 'config', 'controlOptions', 'dataSources', 'figure', 'loadFigure', 'logoSrc', 'logoStyle', 'saveState', 'structureOptions', 'style', 'styleOptions', 'traceOptions']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'annotateOptions', 'config', 'controlOptions', 'dataSources', 'figure', 'loadFigure', 'logoSrc', 'logoStyle', 'saveState', 'structureOptions', 'style', 'styleOptions', 'traceOptions']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashChartEditor, self).__init__(**args)

setattr(DashChartEditor, "__init__", _explicitize_args(DashChartEditor.__init__))
