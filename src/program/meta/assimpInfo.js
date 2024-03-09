import {Program} from "../../Program.js";

export class assimpInfo extends Program
{
	website = "https://github.com/assimp/assimp";
	package = "media-libs/assimp";
	bin     = "assimp";
	args    = r => ["info", r.inFile(), "--silent"];
	post    = r =>
	{
		const meta = {};
	
		const NUMS = ["nodes", "meshes", "animations", "materials", "cameras", "lights", "vertices", "faces", "bones"];
		r.stdout.trim().split("\n").filter(v => !!v).forEach(infoLine =>
		{
			const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {})?.groups;
			if(!infoProps)
				return;

			const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
			if(NUMS.includes(propKey))
				meta[propKey] = +infoProps.val;
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
