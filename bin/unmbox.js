import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {path, readLines} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.mbox> as a standard unix mailbox and extracts each message into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "MBOX file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const SEP_REGS =
[
	/^From (?<sender>.+) (?<timestamp>(?<dayOfWeek>Sun|Mon|Tue|Wed|Thu|Fri|Sat) (?<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?<day>[\d ]\d) (?<hour>[\d ]\d):(?<minute>[\d ]\d):(?<second>[\d ]\d) (?<year>\d{4}))$/,
	/^From (?<sender>[^ ]+) (?<timestamp>.+)$/
];

let msgCount = 0;

let msg = {};
let prevLineEmpty = true;

const inputFile = await Deno.open(argv.inputFilePath);
for await(const line of readLines(inputFile))
{
	if(line.trim().length===0)
	{
		// Only add the blank line if we have a msg right now. Handles mbox files that start with some blank lines
		if(msg.lines)
			msg.lines.push(line);

		prevLineEmpty = true;
		continue;
	}

	let sepMatch = null;
	for(const SEP_REG of SEP_REGS)
	{
		sepMatch = line.trim().match(SEP_REG);
		if(sepMatch)
			break;
	}

	if(sepMatch && prevLineEmpty)
	{
		if(Object.keys(msg).length>0)
		{
			msg.lines.pop();	// Our last message line was empty and was the end of message line, so just pop it off and discard it
			await fileUtil.writeTextFile(path.join(argv.outputDirPath, `${Number(msgCount++).toString().padStart(6, "0")}_${msg.meta.sender.innerTruncate(30)}_${msg.meta.timestamp}.msg`), msg.lines.join("\r\n"));
		}

		msg = {meta : {sender : sepMatch.groups.sender, timestamp : sepMatch.groups.timestamp}, lines : []};
		continue;
	}

	prevLineEmpty = false;

	msg.lines.push(line);
}

inputFile.close();
