import {Program} from "../../Program.js";

export class acorn2sfd extends Program
{
	website   = "https://fontforge.org";
	package   = "media-gfx/fontforge";
	bin       = "acorn2sfd";
	args      = r => [r.f.input.dir];
	cwd       = r => r.outDir();
	renameOut = true;
	chain     = "fontforge";
}
