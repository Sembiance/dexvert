"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://winworldpc.com/product/fantavision/1x-dos",
	unsafe  : true
};

exports.dos = () => "FANTAVSN/PLAYER.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = (state, p, r) => ({
	includeDir : true,
	autoExec   : [`COPY ${r.args[0].toUpperCase()} FANTAVSN\\F.MVE`, "CD FANTAVSN", `PLAYER.EXE`],
	timeout    : XU.SECOND*40,
	video      : path.join(state.output.absolute, `${state.input.name}.mp4`)
});
