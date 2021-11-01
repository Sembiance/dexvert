"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Mac OS X Folder Info",
	ext            : [".ds_store"],
	magic          : ["Mac OS X folder information"]
};

exports.steps = [() => ({program : "dsstoreinfo"})];
