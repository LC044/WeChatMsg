from ..types import Optional, Sequence, Union


class HTML:
    def __init__(self, data: Optional[str] = None):
        self.data = data

    def _repr_html_(self):
        return self.data

    def __html__(self):
        return self._repr_html_()


_lib_t1 = """new Promise(function(resolve, reject) {
    var script = document.createElement("script");
    script.onload = resolve;
    script.onerror = reject;
    script.src = "%s";
    document.head.appendChild(script);
}).then(() => {
"""

_lib_t2 = """
});"""

_css_t = """var link = document.createElement("link");
    link.ref = "stylesheet";
    link.type = "text/css";
    link.href = "%s";
    document.head.appendChild(link);
"""


class Javascript:
    def __init__(
            self,
            data: Optional[str] = None,
            lib: Optional[Union[str, Sequence]] = None,
            css: Optional[Union[str, Sequence]] = None,
    ):
        if isinstance(lib, str):
            lib = [lib]
        elif lib is None:
            lib = []
        if isinstance(css, str):
            css = [css]
        elif css is None:
            css = []
        self.lib = lib
        self.css = css
        self.data = data or ""

    def _repr_javascript_(self):
        r = ""
        for c in self.css:
            r += _css_t % c
        for d in self.lib:
            r += _lib_t1 % d
        r += self.data
        r += _lib_t2 * len(self.lib)
        return r
