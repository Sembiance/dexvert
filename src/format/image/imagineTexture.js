import {Format} from "../../Format.js";

export class imagineTexture extends Format
{
	name        = "Imagine Texture";
	website     = "http://fileformats.archiveteam.org/wiki/Imagine_Texture_File";
	ext         = [".itx"];
	magic       = ["Imagine for DOS Texture"];
	unsupported = true;	// The format isn't actually raster, but rather includes x86 machine code that procedurally generates the textures. see vibe/legacy/imagineTexture/ for an initial stab at it (without exucting the code)
}
