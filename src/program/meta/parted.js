import {xu} from "xu";
import {Program} from "../../Program.js";

export class parted extends Program
{
	website = "https://www.gnu.org/software/parted/";
	package = "sys-block/parted";
	bin     = "parted";
	args    = r => ["--machine", "--json", r.inFile(), "unit", "B", "print"];
	post    = r =>
	{
		const imageInfo = xu.parseJSON(r.stdout.trim());
		const sectorSize = imageInfo?.disk?.["logical-sector-size"];
		if(!sectorSize)
			return;

		const parseSize = function parseSize(str)
		{
			const unit = str.match(/[a-zA-Z]+$/)[0];
			const sizeNum = +str.slice(0, -unit.length);
			switch(unit)
			{
				case "B":
					return sizeNum;
				// Since switching to "unit B" then these other sizes should no longer be used, which is good because they ended up losing precision (see rawPartition/Warez 3.img)
				case "kB":
					return sizeNum*1000;
				case "MB":
					return sizeNum*(1000*1000);
				case "GB":
					return sizeNum*(1000*1000*1000);
				default:
					throw new Error(`Unknown unit ${unit} for string: ${str}`);
			}
		};

		const partitions = [];
		for(const partInfo of imageInfo.disk?.partitions || [])
			partitions.push({start : parseSize(partInfo.start), end : parseSize(partInfo.end), size : parseSize(partInfo.size), type : partInfo.type, number : partInfo.number, name : partInfo.name, filesystem : partInfo.filesystem});

		if(partitions.length)
			r.meta.partitions = partitions;
	};
	renameOut = false;
}
