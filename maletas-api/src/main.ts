import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as cors from 'cors';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Configurar CORS para Angular
  // app.use(cors({
  //   origin: 'http://localhost:4200',
  //   credentials: true
  // }));

  app.enableCors();

  await app.listen(process.env.PORT ?? 3000);
  console.log('🚀 Backend running on http://localhost:' + process.env.PORT);

}
bootstrap();
