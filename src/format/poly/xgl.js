import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class xgl extends Format
{
	name       = "XGL ";
	website    = "https://people.math.sc.edu/Burkardt/data/xgl/xgl_spec.html";
	ext        = [".xgl"];
	idCheck    = async inputFile => inputFile.size>64 && (await fileUtil.readFileBytes(inputFile.absolute, 64)).indexOfX(new TextEncoder().encode("<WORLD>"))!==-1;
	converters = ["assimp"];
}
