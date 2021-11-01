/*
import {Format} from "../../Format.js";

export class nrg extends Format
{
	name = "Nero CD Image";
	website = "http://fileformats.archiveteam.org/wiki/NRG";
	ext = [".nrg"];
	magic = ["Nero CD image"];
	priority = 0;
	converters = [["nrg2iso",{"program":"dexvert","flags":{"deleteInput":true}}],"UniExtract"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require("../../C.js");

exports.meta =
{
	name    : "Nero CD Image",
	website : "http://fileformats.archiveteam.org/wiki/NRG",
	ext     : [".nrg"],
	magic   : ["Nero CD image"],
	priority : C.PRIORITY.TOP	// NRG is often mis-identified as ISO
};

exports.converterPriority =
[
	["nrg2iso", {program : "dexvert", flags : {deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.iso`), state.output.absolute])}],
	"UniExtract"
];

*/
