"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Blazing Paddles - Font",
	website : "http://fileformats.archiveteam.org/wiki/Blazing_Paddles",
	ext     : [".chr"]
};

exports.steps = [() => ({program : "recoil2png"})];
