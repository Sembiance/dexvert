"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://poppler.freedesktop.org/",
	gentooPackage  : "app-text/poppler",
	gentooUseFlags : "cairo curl cxx introspection jpeg jpeg2k lcms png qt5 tiff utils",
	informational  : true
};

exports.bin = () => "pdfinfo";
exports.args = state => ([state.input.filePath]);
