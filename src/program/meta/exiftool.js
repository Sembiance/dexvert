import {xu} from "xu";
import {Program} from "../../Program.js";

export class exiftool extends Program
{
	website   = "https://exiftool.org/";
	package   = "media-libs/exiftool";
	bin       = "exiftool";
	args      = r => ["-quiet", "-json", r.inFile()];
	post      = r =>
	{
		const meta = xu.parseJSON(r.stdout?.trim() || "[{}]")?.[0] || {};
		for(const key of ["SourceFile", "ExifToolVersion", "FileName", "Directory", "FileSize", "FileModifyDate", "FileAccessDate", "FileInodeChangeDate", "FilePermissions", "TimeStamp", "FileTypeExtension", "MIMEType", "Warning"])
			delete meta[key];
		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
