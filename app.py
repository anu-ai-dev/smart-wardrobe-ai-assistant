import gradio as gr
from smart_wardrobe.feature1.user_management import user_management_interface
from smart_wardrobe.feature2.wardrobe_management import wardrobe_management_interface
from smart_wardrobe.feature3.outfit_recommendation import outfit_recommendation_interface
from smart_wardrobe.feature4.discover_shopping_platforms import platform_interface
from smart_wardrobe.feature5.laundry_tracker import laundry_interface
from smart_wardrobe.feature6.styling_suggestions import styling_suggestions_interface
from smart_wardrobe.feature7.packing_assistant import packing_assistant_interface

def main():
    print("Smart Wardrobe Application") 

    with gr.Blocks() as demo:  # Create a main Gradio app
        with gr.Tab("User Management"):
            user_management_interface.render()
        with gr.Tab("Wardrobe Management"):
            wardrobe_management_interface.render()
        with gr.Tab("Outfit Recommendation"):  
           outfit_recommendation_interface.render()
        with gr.Tab("Shopping Platforms"):
          platform_interface.render()
        with gr.Tab("Laundry Tracker"):
           laundry_interface.render()
        with gr.Tab("Styling Suggestions"):
          styling_suggestions_interface.render()
        with gr.Tab("Packing Assistant"):
          packing_assistant_interface.render()
 


    demo.launch()  # Launch the combined app

if __name__ == "__main__":
    main()

