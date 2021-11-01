/*
import {Format} from "../../Format.js";

export class news extends Format
{
	name = "Newsgroup Content";
	magic = ["saved news"];
	unsafe = true;

steps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	readline = require("readline"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name   : "Newsgroup Content",
	magic  : ["saved news"],
	unsafe : true
};

const SEP_REGS =
[
	/^Article (?<num>\d+) of (?<newsgroup>[^:]+):$/
];

exports.steps =
[
	() => (state, p, cb) =>
	{
		let msgCount = 0;

		tiptoe(
			function extractMessages()
			{
				let msg = {};
				let prevLineEmpty = true;

				const rl = readline.createInterface({input : fs.createReadStream(state.input.absolute), terminal : false});
				rl.on("line", line =>
				{
					if(line.trim().length===0)
					{
						// Only add the blank line if we have a msg right now. Handles mbox files that start with some blank lines
						if(msg.lines)
							msg.lines.push(line);

						prevLineEmpty = true;
						return;
					}

					const sepMatch = SEP_REGS.reduceOnce(SEP_REG => (line.match(SEP_REG) || undefined));
					if(sepMatch && prevLineEmpty)
					{
						if(Object.keys(msg).length>0)
						{
							msg.lines.pop();	// Our last message line was empty and was the end of message line, so just pop it off and discard it
							fs.writeFile(path.join(state.output.absolute, `${msg.meta.newsgroup}_${msg.meta.num}_${Number(msgCount++).toString().padStart(6, "0")}.msg`), msg.lines.join("\r\n"), XU.UTF8, this.parallel());
						}

						msg = {meta : {newsgroup : sepMatch.groups.newsgroup, num : sepMatch.groups.num}, lines : []};
						return;
					}

					prevLineEmpty = false;

					if(msg.lines)
						msg.lines.push(line);
				});
				rl.on("close", this.parallel());
			},
			cb
		);
	}
];

*/
