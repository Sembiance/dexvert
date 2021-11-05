import {Format} from "../../Format.js";

export class revisableFormText extends Format
{
	name           = "IBM Revisable-Form Text";
	ext            = [".rft", ".dca"];
	forbidExtMatch = true;
	magic          = [/Revisable Form Text/];
	converters     = ["fileMerlin", "word97 -> dexvert[asFormat:document/wordDoc][deleteInput]"]
}

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name           : "IBM Revisable-Form Text",
	ext            : [".rft", ".dca"],
	forbidExtMatch : true,
	magic          : []
};

exports.converterPriority =
[
	"fileMerlin",
	["word97", {program : "dexvert", flags : {asFormat : "document/wordDoc", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.doc`), state.output.absolute])}]
];

*/
