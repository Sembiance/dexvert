/*
import {Format} from "../../Format.js";

export class doomMUS extends Format
{
	name = "Doom/Heretic Music";
	website = "http://fileformats.archiveteam.org/wiki/Doom_MUS";
	ext = [".mus"];
	forbidExtMatch = true;
	magic = ["Doom/Heretic music"];
	converters = [["doomMUS2mid",{"program":"dexvert","flags":{"deleteInput":true}}]]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name           : "Doom/Heretic Music",
	website        : "http://fileformats.archiveteam.org/wiki/Doom_MUS",
	ext            : [".mus"],
	forbidExtMatch : true,
	magic          : ["Doom/Heretic music"]
};

exports.converterPriority =
[
	["doomMUS2mid", {program : "dexvert", flags : {deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.mid`), state.output.absolute])}]
];

*/
