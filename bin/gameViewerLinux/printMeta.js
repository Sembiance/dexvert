import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import {XLog} from "xlog";
import {path} from "std";

const xlog = new XLog();

const formats = xu.parseJSON(await fileUtil.readTextFile(path.join(import.meta.dirname, "meta.json")));
const longestFilename = formats.map(o => o.filename.length).max() + 4;
for(const format of formats)
{
	if((/[^\x00-\x7F]/).test(format.NAME))	// eslint-disable-line no-control-regex, unicorn/no-hex-escape
	{
		const {stdout} = await runUtil.run("trans", ["-b", "ru:en", format.NAME]);
		format.NAME = stdout.trim();
	}

	format.fullName = `${format.filename}${" ".repeat(longestFilename - format.filename.length)}${format.NAME}`;
}

const longestName = formats.map(o => o.fullName.length).max() + 4;
for(const format of formats.sortMulti([o => o.filename]))
{
	for(const type of format.TYPES)
	{
		if((/[^\x00-\x7F]/).test(type[0]))	// eslint-disable-line no-control-regex, unicorn/no-hex-escape
		{
			const {stdout} = await runUtil.run("trans", ["-b", "ru:en", type[0]]);
			type[0] = stdout.trim();
		}

		if(type[0]===format.NAME)
			type[0] = "";
	}

	let seenLine = false;
	const longestType = format.TYPES.map(t => t[1].length).max() + 4;
	for(const type of format.TYPES.sortMulti([o => o[0]]))
	{
		const line = seenLine ? [" ".repeat(longestName)] : [format.fullName, " ".repeat(longestName - format.fullName.length)];
		seenLine = true;
		line.push(type[1], " ".repeat(longestType - type[1].length), type[0]);
		console.log(line.join(""));
	}
}
