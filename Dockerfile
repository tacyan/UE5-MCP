FROM python:3.10-slim

LABEL maintainer="MCP Development Team"
LABEL description="Model Context Protocol for UE5 and Blender integration"

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libgl1-mesa-dev \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt .
COPY *.py .
COPY templates/ ./templates/
COPY blender_scripts/ ./blender_scripts/

# 必要なディレクトリを作成
RUN mkdir -p exports imports logs assets temp

# Pythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# 環境変数の設定（デフォルト値）
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8080
ENV DEBUG=false
ENV BLENDER_ENABLED=true
ENV BLENDER_PORT=8081
ENV UE5_ENABLED=true
ENV UE5_PORT=8082
ENV BLENDER_MCP_PORT=9081
ENV UE5_MCP_PORT=9082

# ポートの公開
EXPOSE 8080 8081 8082 9081 9082

# エントリポイントの設定
ENTRYPOINT ["python", "run_mcp.py"]

# デフォルト引数
CMD ["server"] 
