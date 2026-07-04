import sys

from app.models.product import Product
from app.workflows.create_video import CreateVideoWorkflow


def main():
    workflow = CreateVideoWorkflow()

    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"=== Pipeline: URL → Product → Script → Audio → Video ===\n")
        print(f"URL: {url}\n")
        result = workflow.run_from_url(url)
    else:
        print("=== Pipeline demo (không có URL) ===\n")
        product = Product(
            name="Quạt mini cầm tay",
            price="199.000đ",
            description="Pin 4000mAh\n100 cấp gió\nNhỏ gọn\nDùng 8 tiếng",
            target_customer="Sinh viên và nhân viên văn phòng",
            images=[],
        )
        result = workflow.run_from_product(product)

    print("=== PRODUCT ===")
    print(result.product.model_dump_json(indent=2, ensure_ascii=False))
    print()

    print("=== SCRIPT ===")
    print(result.script.model_dump_json(indent=2, ensure_ascii=False))
    print()

    print("=== AUDIO ===")
    for scene in result.voice.scenes:
        print(f"  Scene {scene.scene_id}: {scene.file_path} ({scene.duration:.1f}s)")
    print()

    print("=== VIDEO ===")
    print(f"  File: {result.video.file_path}")
    print(f"  Duration: {result.video.duration:.1f}s")
    print(f"  Size: {result.video.width}x{result.video.height}")
    print()
    print(f"Output folder: {result.run_dir}")


if __name__ == "__main__":
    main()
