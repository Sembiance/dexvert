"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	readline = require("readline"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name    : "Mailbox",
	website : "http://fileformats.archiveteam.org/wiki/Mbox",
	ext     : [".mbox"],
	magic   : ["Standard Unix Mailbox"],
	unsafe  : true
};

const SEP_REGS =
[
	/^From (?<sender>.+) (?<timestamp>(?<dayOfWeek>Sun|Mon|Tue|Wed|Thu|Fri|Sat) (?<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?<day>[\d ]\d) (?<hour>[\d ]\d):(?<minute>[\d ]\d):(?<second>[\d ]\d) (?<year>\d{4}))$/,
	/^From (?<sender>[^ ]+) (?<timestamp>.+)$/
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
							fs.writeFile(path.join(state.output.absolute, `${Number(msgCount++).toString().padStart(6, "0")}_${msg.meta.sender}_${msg.meta.timestamp}.msg`), msg.lines.join("\r\n"), XU.UTF8, this.parallel());
						}

						msg = {meta : {sender : sepMatch.groups.sender, timestamp : sepMatch.groups.timestamp}, lines : []};
						return;
					}

					prevLineEmpty = false;

					msg.lines.push(line);
				});
				rl.on("close", this.parallel());
			},
			cb
		);
	}
];
