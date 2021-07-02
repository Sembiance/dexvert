"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Macromedia Director Cast",
	website        : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext            : [".cst"],
	forbidExtMatch : true,
	magic          : ["Macromedia Director project"],
	weakMagic      : true,
	keepFilename   : "extras",
	filesOptional  : (state, otherFiles, otherDirs=[]) => { XU.log`otherFiles ${otherFiles} otherDirs ${otherDirs}`; return otherDirs.filter(otherDir => otherDir.toLowerCase()==="xtras"); },
	notes          : "Several cast file types are not yet support. Mainly because I haven't encountered them yet. Also 'xtras' are not supported yet. See macromediaDirector.js for more info."
};

exports.converterPriorty = ["macromediaDirector"];
