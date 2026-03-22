import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ConfigModule } from '@nestjs/config';
import { MaletasModule } from './maletas/maletas.module';

@Module({
  imports: [ConfigModule.forRoot(), MaletasModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
