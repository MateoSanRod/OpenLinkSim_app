#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 screenSize;

void main() {
    vec2 inverseVP = 1.0 / screenSize;

    vec3 color = texture(screenTexture, TexCoords).rgb;
    vec3 luma = vec3(0.299, 0.587, 0.114);

    float lumaNW = dot(texture(screenTexture, TexCoords + vec2(-1.0, -1.0) * inverseVP).rgb, luma);
    float lumaNE = dot(texture(screenTexture, TexCoords + vec2(1.0, -1.0) * inverseVP).rgb, luma);
    float lumaSW = dot(texture(screenTexture, TexCoords + vec2(-1.0, 1.0) * inverseVP).rgb, luma);
    float lumaSE = dot(texture(screenTexture, TexCoords + vec2(1.0, 1.0) * inverseVP).rgb, luma);
    float lumaM = dot(texture(screenTexture, TexCoords).rgb, luma);

    float edgeDetect = abs(lumaNW + lumaNE - lumaSW - lumaSE);

    if (edgeDetect > 0.1) {
        color *= 0.8;  // Apply blur to the edge to reduce aliasing
    }

    FragColor = vec4(color, 1.0);
}
