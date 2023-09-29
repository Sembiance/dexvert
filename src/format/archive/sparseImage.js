import {xu} from "xu";
import {Format} from "../../Format.js";

export class sparseImage extends Format
{
	name        = "Apple Sparse Disk Image";
	website     = "https://en.wikipedia.org/wiki/Sparse_image";
	ext         = [".sparseimage"];
	magic       = ["Apple Sparse disk image"];
	unsupported = true;
	notes       = `No known linux converter that I could find. Could emulate MacOS X and do: https://github.com/torarnv/sparsebundlefs/issues/7#issuecomment-326625187`;
}
