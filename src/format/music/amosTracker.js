"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name    : "AMOS Tracker Bank",
	website : "https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format",
	ext     : [".abk"],
	magic   : ["AMOS Memory Bank, Tracker format"]
};

exports.preSteps = [(state, p) => p.util.program.run("extractAmBk")];

exports.converterPriority = (s0, p0) => (p0.util.program.getRan(s0, "extractAmBk").modFilePath ? [
	{program : "xmp", argsd : (state, p) => ([p.util.program.getRan(state, "extractAmBk").modFilePath]) },
	{program : "awaveStudio", argsd : (state, p) => ([p.util.program.getRan(state, "extractAmBk").modFilePath]) }
] : []);

exports.postSteps =
[
	() => (state, p, cb) =>
	{
		tiptoe(
			function runModInfo()
			{
				p.util.program.run("modInfo", {argsd : s0 => ([p.util.program.getRan(s0, "extractAmBk").modFilePath])})(state, p, this);
			},
			function saveModInfo(r)
			{
				state.input.meta.music = r.meta;
				this();
			},
			cb
		);
	}
];
