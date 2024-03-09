import {Program} from "../../Program.js";

export class assimp extends Program
{
	website   = "https://github.com/assimp/assimp";
	package   = "media-libs/assimp";
	bin       = "assimp";
	args      = async r => ["export", r.inFile(), await r.outFile("out.glb")];		// flags: https://github.com/assimp/assimp/blob/master/tools/assimp_cmd/Main.cpp
	renameOut = true;
	// Attempts to compile this under windows with Cinema 4D support failed. I was able to get assimp to compile with the SDK and show that it supports .c4d, but couldn't actually load and convert any .c4d files
}
