/*
import {Format} from "../../Format.js";

export class dr2d extends Format
{
	name = "DR2D Image";
	website = "https://wiki.amigaos.net/wiki/DR2D_IFF_2-D_Objects";
	ext = [".dr2d"];
	magic = ["IFF data, DR2D 2-D object","IFF 2-D Object standard format"];
	converters = [["DR2DtoPS",{"program":"inkscape"}]]

post = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "DR2D Image",
	website : "https://wiki.amigaos.net/wiki/DR2D_IFF_2-D_Objects",
	ext     : [".dr2d"],
	magic   : ["IFF data, DR2D 2-D object", "IFF 2-D Object standard format"]
};

exports.converterPriority =
[
	["DR2DtoPS", {program : "inkscape", argsd : state => ([path.join(state.output.absolute, `${state.input.name}.ps`)])}]
];

exports.post = (state, p, cb) => p.util.file.unlink(path.join(state.output.absolute, `${state.input.name}.ps`))(state, p, cb);

*/