import {Program} from "../../Program.js";

export class vgmstream extends Program
{
	website   = "https://github.com/vgmstream/vgmstream";
	package   = "media-sound/vgmstream-cli";
	flags   = {
		extractAll : "If set to true, will extract all streams in the file. This has to be opt in because vgmstream-cli won't output anything if there is only one stream and you try to extract all. Default: false"
	};
	bin       = "vgmstream-cli";
	args      = async r => [...(r.flags.extractAll ? ["-S", "0"] : []), "-o", await r.outFile("out_?s.wav"), "-i", r.inFile()];
	chain     = "sox";
	renameOut  = {
		alwaysRename : true,
		regex        : /out_(?<num>\d+)\.wav$/,
		renamer      : [({newName}, {num}) => [newName, "_", num, ".wav"]]
	};
}
