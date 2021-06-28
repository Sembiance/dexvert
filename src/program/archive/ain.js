"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.sac.sk/download/pack/ain232.exe"
};

exports.dos = () => "AIN.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);
exports.dosData = (state, p, r) => ({autoExec : ["CD OUT", `..\\AIN.EXE x ${r.args}`], keys : [["Return"]], keyOpts : {delay : XU.SECOND*4}});
