import {Program} from "../../Program.js";

const _OUT_TYPES = {
	threeDStudio   : 2,
	direct3DObject : 100
};

const _OUT_TYPE_DEFAULT = "threeDStudio";

export class i3DConverter extends Program
{
	website   = "http://www.i3dconverter.com/";
	bin       = Program.binPath("i3DConverter/i3DConverter");
	flags   = {
		outType : "Specify which format to output to"
	};
	args      = r => [r.inFile({absolute : true}), _OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].toString(), "-exportpath", r.outDir({absolute : true})];		// flags: http://www.i3dconverter.com/features.html
	renameOut = true;
}
