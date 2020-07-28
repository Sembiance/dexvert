"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	readline = require("readline"),
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	name        : "Internet Message Format",
	website     : "http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format",
	ext         : [".eml", ".msg"],
	magic       : ["E-Mail message", "news or mail", "news, ASCII text"]
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		// imf format: https://tools.ietf.org/rfc/rfc2822.txt
		const msg = {header : {}};
		let failed = false;

		tiptoe(
			function convertMessage()
			{
				const rl = readline.createInterface({input : fs.createReadStream(state.input.absolute), terminal : false});
				let prevHeaderKey = null;
				rl.on("line", line =>
				{
					console.log(line);
					if(failed)
						return;

					// If we have an empty line and no body yet, then it's time to start the body
					if(line.trim().length===0 && !msg.hasOwnProperty("bodyLines"))
					{
						if(Object.keys(msg.header).length===0)
						{
							failed = true;
							return;
						}
						msg.bodyLines = [];
						return;
					}

					// If we have a body, then all lines just go into that
					if(msg.hasOwnProperty("bodyLines"))
					{
						msg.bodyLines.push(line);
						return;
					}

					// If we have an empty line in the header, just ignore it, might be empty lines at start of file
					if(line.trim().length===0)
						return;

					// See if we are starting a new header with the format: "<key>: <val>"
					const headerMatch = line.match(/^(?<key>[^:]+): (?<val>.+)$/);
					if(headerMatch)
					{
						prevHeaderKey = headerMatch.groups.key;
						msg.header[prevHeaderKey] = headerMatch.groups.val;
						return;
					}

					// See if this is a continuation of a previous header with the format: " <val>"
					const prevHeaderMatch = line.match(/^ (?<val>.+)$/);
					if(prevHeaderMatch && prevHeaderKey)
					{
						msg.header[prevHeaderKey] += ` ${prevHeaderMatch.groups.val}`;
						return;
					}

					failed = true;
				});
				rl.on("close", this);
			},
			function saveJSON()
			{
				if(failed)
					return this();

				msg.body = msg.bodyLines.join("\n");
				delete msg.bodyLines;

				fs.writeFile(path.join(state.output.absolute, `${state.input.name}.json`), JSON.stringify(msg), XU.UTF8, this);
			},
			cb
		);
	}
];
