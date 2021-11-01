"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Novell/C-Worthy Message Librarian",
	ext            : [".msg", ".dat"],
	forbidExtMatch : true,
	magic          : [/^Novell [Mm]essage [Ll]ibrarian [Dd]ata/, "C-Worthy Message Librarian Data"]
};

exports.converterPriority = ["strings"];
