import { PartialType } from '@nestjs/mapped-types';
import { CreateMaletaDto } from './create-maleta.dto';

export class UpdateMaletaDto extends PartialType(CreateMaletaDto) {}
