import { Module } from '@nestjs/common';
import { MaletasService } from './maletas.service';
import { MaletasController } from './maletas.controller';

@Module({
  controllers: [MaletasController],
  providers: [MaletasService],
})
export class MaletasModule {}
