/*
import {Format} from "../../Format.js";

export class revisableFormText extends Format
{
	name = "IBM Revisable-Form Text";
	ext = [".rft",".dca"];
	forbidExtMatch = true;
	magic = [{}];
	converters = ["fileMerlin",["word97",{"program":"dexvert","flags":{"asFormat":"document/wordDoc","deleteInput":true}}]]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name           : "IBM Revisable-Form Text",
	ext            : [".rft", ".dca"],
	forbidExtMatch : true,
	magic          : [/Revisable Form Text/]
};

exports.converterPriority =
[
	"fileMerlin",
	["word97", {program : "dexvert", flags : {asFormat : "document/wordDoc", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.doc`), state.output.absolute])}]
];

*/
