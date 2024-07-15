import {Program} from "../../Program.js";

export class ripmime extends Program
{
	website        = "https://github.com/inflex/ripMIME";
	package        = "net-mail/ripmime";
	bin            = "ripmime";
	forbidChildRun = true;
	args           = r => ["-e", "__headers__.txt", "-i", r.inFile(), "-d", r.outDir(), "-p", "part", "--mailbox", "--name-by-type"];
	renameOut      = {
		alwaysRename : true,
		regex        : /part((?<prefix>[^-]+)-)?(?<type>alternative|gif|jpeg|html|mixed|plain|text)(?<num>\d+)$/,
		renamer      :
		[
			({fn}, {prefix, type, num}) => (type?.length ? [prefix || type, num.toString().padStart(4, "0"), ".", ({alternative : "out", jpeg : "jpg", mixed : "out", plain : "txt", text : "txt"}[type] || type)] : [fn])
		]
	};
}
