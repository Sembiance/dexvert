import {Format} from "../../Format.js";

export class dosBackup33File extends Format
{
	name             = "DOS BACKUP 3.3 file";
	website          = "http://fileformats.archiveteam.org/wiki/BACKUP_(MS-DOS)";
	filename         = [/^backup\.\d{3}$/i];
	auxFiles         = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`control${input.ext.toLowerCase()}`);
	confidenceAdjust = () => 100;
	converters       = ["deark[module:dosbackup33]"];
	unsupported      = true; // couldn't get it working
}
