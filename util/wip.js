"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs");

process.exit(0);

const processDataFilePath = path.join(__dirname, "..", "test", "data", "process.json");

const data = JSON.parse(fs.readFileSync(processDataFilePath, XU.UTF8));
Object.values(data).forEach(result =>
{
	if(!result.files)
		return;
		
	Object.mapInPlace(result.files, (k, v) => ([k, {sum : v}]));
});

fs.writeFileSync(processDataFilePath, JSON.stringify(data), XU.UTF8);
