import {xu} from "xu";
import {Program} from "../../Program.js";

export class glTFValidator extends Program
{
	website = "https://github.com/KhronosGroup/glTF-Validator";
	package = "media-gfx/glTF-Validator";
	bin     = "gltf_validator";
	args    = r => ["--no-validate-resources", "--stdout", r.inFile()];
	post    = r =>
	{
		const data = xu.parseJSON(r.stdout);
		if(!data)
			return;

		const meta = {};
		meta.vertices = data?.info?.totalVertexCount;
		meta.materials = data?.info?.materialCount;
		meta.animations = data?.info?.animationCount;

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
