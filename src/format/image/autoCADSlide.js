/*
import {Format} from "../../Format.js";

export class autoCADSlide extends Format
{
	name = "AutoCAD Slide";
	website = "http://fileformats.archiveteam.org/wiki/AutoCAD_Slide";
	ext = [".sld"];
	magic = [{}];
	converters = [["sldtoppm",{"program":"dexvert","flags":{"deleteInput":true}}]]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "AutoCAD Slide",
	website : "http://fileformats.archiveteam.org/wiki/AutoCAD_Slide",
	ext     : [".sld"],
	magic   : [/^AutoCAD Slide$/]
};

exports.converterPriority =
[
	["sldtoppm", {program : "dexvert", flags : {deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.ppm`), state.output.absolute])}]
];

*/
